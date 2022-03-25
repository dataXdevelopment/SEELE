import { Duration, Stack, StackProps } from 'aws-cdk-lib';
import { Construct } from 'constructs';
import * as lambda from 'aws-cdk-lib/aws-lambda';
import { Queue } from 'aws-cdk-lib/aws-sqs';
import { SqsDestination } from 'aws-cdk-lib/aws-lambda-destinations';
export class DeranaStack extends Stack {
  constructor(scope: Construct, id: string, props?: StackProps) {
    super(scope, id, props);

    // The code that defines your stack goes here

    // example resource
    // const queue = new sqs.Queue(this, 'DeranaQueue', {
    //   visibilityTimeout: cdk.Duration.seconds(300)
    // });

    const queue = new Queue(this, 'DeranaQueriesQueue', {
    })

    
    
    const role = fn.role;
    if (role !== undefined) queue.grantConsumeMessages(role);
  }
}
