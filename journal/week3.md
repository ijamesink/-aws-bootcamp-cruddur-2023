# Week 3 — Decentralized Authentication

## provision AWS Amplify

install the amplify library in our frontend-react directory
npm i aws-amplify --save

## install Amplify
added the amplify import statement to our App.jss block of codes

    import { Amplify } from 'aws-amplify';

    Amplify.configure({
    "AWS_PROJECT_REGION": process.env.REACT_APP_AWS_PROJECT_REGION,
    "aws_cognito_identity_pool_id": process.env.REACT_APP_AWS_COGNITO_IDENTITY_POOL_ID,
    "aws_cognito_region": process.env.REACT_APP_AWS_COGNITO_REGION,
    "aws_user_pools_id": process.env.REACT_APP_AWS_USER_POOLS_ID,
    "aws_user_pools_web_client_id": process.env.REACT_APP_CLIENT_ID,
    "oauth": {},
    Auth: {
        // We are not using an Identity Pool
        // identityPoolId: process.env.REACT_APP_IDENTITY_POOL_ID, // REQUIRED - Amazon Cognito Identity Pool ID
        region: process.env.REACT_AWS_PROJECT_REGION,           // REQUIRED - Amazon Cognito Region
        userPoolId: process.env.REACT_APP_AWS_USER_POOLS_ID,         // OPTIONAL - Amazon Cognito User Pool ID
        userPoolWebClientId: process.env.REACT_APP_AWS_USER_POOLS_WEB_CLIENT_ID,   // OPTIONAL - Amazon Cognito Web Client ID (26-char alphanumeric string)
    }
    });

## Conditionally show logged components
 Add below import code to the homefeedpage.js under pages

        import { Auth } from 'aws-amplify';

        // set a state
        const [user, setUser] = React.useState(null);

        // check if we are authenicated
        const checkAuth = async () => {
        Auth.currentAuthenticatedUser({
            // Optional, By default is false. 
            // If set to true, this call will send a 
            // request to Cognito to get the latest user data
            bypassCache: false 
        })
        .then((user) => {
            console.log('user',user);
            return Auth.currentAuthenticatedUser()
        }).then((cognito_user) => {
            setUser({
                display_name: cognito_user.attributes.name,
                handle: cognito_user.attributes.preferred_username
            })
        })
        .catch((err) => console.log(err));
        };

        // check when the page loads if we are authenicated
        React.useEffect(()=>{
        loadData();
        checkAuth();
        }, [])

