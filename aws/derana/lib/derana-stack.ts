import { Duration, Stack, StackProps } from 'aws-cdk-lib';
import { Construct } from 'constructs';
import { Cluster, ContainerImage, CpuArchitecture, FargateTaskDefinition, LogDriver, OperatingSystemFamily } from 'aws-cdk-lib/aws-ecs';
import { PublicSubnet, SecurityGroup, SubnetType, Vpc } from 'aws-cdk-lib/aws-ec2';
import { RuntimeFamily } from 'aws-cdk-lib/aws-lambda';
import { EcsFargateLaunchTarget, EcsRunTask, EvaluateExpression } from 'aws-cdk-lib/aws-stepfunctions-tasks';
import { IntegrationPattern, JsonPath, Map, Pass, StateMachine } from 'aws-cdk-lib/aws-stepfunctions';
export class DeranaStack extends Stack {
  constructor(scope: Construct, id: string, props?: StackProps) {
    super(scope, id, props);


    const vpc = new Vpc(this, 'deranaVPC', {
      cidr: '10.0.0.0/16',
      maxAzs: 1,
      natGateways: 0,

      subnetConfiguration: [
        {
          cidrMask: 16,
          name: 'publicDeranaVPC',
          subnetType: SubnetType.PUBLIC
        }
      ]
    });

    const cluster = new Cluster(this, 'DeranaCluster', {
      clusterName: 'derana-cluster',
      enableFargateCapacityProviders: true,
      vpc: vpc,
    });

    const queryTaskDefinition = new FargateTaskDefinition(this, 'QueryTask', {
      cpu: 256,
      memoryLimitMiB: 512,
      runtimePlatform: {
        operatingSystemFamily: OperatingSystemFamily.LINUX
      },
    });

    const queryContainer = queryTaskDefinition.addContainer('QueryContainer', {
      command: ["python", "index.py", "power cut", "1025"],
      environment: {
        'SPLIT_SIZE': '100',
      },
      logging: LogDriver.awsLogs({ streamPrefix: 'query-fargate' }),
      image: ContainerImage.fromAsset('resources', {
        buildArgs: {
          'FILE_NAME': 'query.py',
        },
      }),
    });

    const scrapeTaskDefinition = new FargateTaskDefinition(this, 'ScrapeTask', {
      cpu: 256,
      memoryLimitMiB: 512,
      runtimePlatform: {
        operatingSystemFamily: OperatingSystemFamily.LINUX
      },
    });

    scrapeTaskDefinition.addContainer('ScrapeContainer', {
      logging: LogDriver.awsLogs({ streamPrefix: 'scrape-fargate' }),
      image: ContainerImage.fromAsset('resources', {
        buildArgs: {
          'FILE_NAME': 'scrape.py',
        },
      }),
    });

    const createQueryParams = new EvaluateExpression(this, 'createQueryParams', {
      expression: `['python', 'index.py', $.query, $.jobId]`,
      resultPath: '$.command'
    })
    const runQueryTask = new EcsRunTask(this, 'RunQueryTask', {
      integrationPattern: IntegrationPattern.WAIT_FOR_TASK_TOKEN,
      cluster,
      taskDefinition: queryTaskDefinition,
      launchTarget: new EcsFargateLaunchTarget(),
      assignPublicIp: true,
      containerOverrides: [
        {
          containerDefinition: queryContainer,
          command: JsonPath.listAt('$.command'),
          environment: [
            {
              name: "TASK_TOKEN_ENV_VARIABLE",
              value: JsonPath.taskToken,
            }
          ]
        }
      ]
    });

    const runScrapeTask = new EcsRunTask(this, 'RunScrapeTask', {
      integrationPattern: IntegrationPattern.RUN_JOB,
      cluster,
      taskDefinition: queryTaskDefinition,
      launchTarget: new EcsFargateLaunchTarget(),
      assignPublicIp: true,
      containerOverrides: [
        {
          containerDefinition: queryContainer,
          environment: [
            {
              name: "TASK_TOKEN_ENV_VARIABLE",
              value: JsonPath.taskToken,
            }
          ]
        }
      ]
    });



    const mapUrls = new Map(this, 'MapUrls', {
      maxConcurrency: 4,
      itemsPath: JsonPath.stringAt('$.urls'),
    });

    mapUrls.iterator(new Pass(this, 'PassState'));


    const definition = createQueryParams.next(
      runQueryTask.next(
        mapUrls
      )
    );

    const stateMachine = new StateMachine(this, 'DeranaStateMachine', {
      definition,
    })

    stateMachine.grantTaskResponse(queryTaskDefinition.taskRole);






  }
}
