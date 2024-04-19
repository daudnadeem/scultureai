from aws_cdk import (
    core
)

from stacks.stack import FastAPIWithCognitoStack

app = core.App()
FastAPIWithCognitoStack(app, "SCultureAiStack")
app.synth()