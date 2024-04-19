# scultureai

Concious of time I am going to keep this brief. I have created a CDK stack that spins up a user pool, dynamo DB, lambda, an API GW, and the permissions (mainly for dynamo)

If you run `cdk deploy` it should show you the URL at the end, at the time of me writing this this is how you can make requests:

`POST` request https://5xyues3u91.execute-api.eu-west-1.amazonaws.com/dev/user/test_user_1/save?text=Entry 3 where user = `test_user_1` and text = `Entry 3`

and

`GET` request https://5xyues3u91.execute-api.eu-west-1.amazonaws.com/dev/user/test_user_1/show to get back all entries for a user.

In a productionised application, the `user_id` would be inherited from the current active user, this can be done very easily using AWS ID Token (where we can extract the user from the token)

In a productionised application I would make use of `poetry` as a dependency management rather than uploading a zip of dependencies (horrible) also, we use bitbuckets pipelines to run our code, for now I have a `pipeline_cicd.sh` file will should do the trick to get everything set up and CDK deploy'd.

I will attach a video with this PR to show the working. I can definitely make more progress but this is all I have mustered up in approx 2 hours (need to get back to work!)

