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

## Implemented the Signin page
Added below code to the signin.js file

    import { Auth } from 'aws-amplify';

    const onsubmit = async (event) => {
    setErrors('')
    event.preventDefault();
    Auth.signIn(email, password)
    .then(user => {
      localStorage.setItem("access_token", user.signInUserSession.accessToken.jwtToken)
      window.location.href = "/"
    })
    .catch(error => {
      if (error.code == 'UserNotConfirmedException') {
        window.location.href = "/confirm"
      }
      setErrors(error.message)
    });
    return false
  }

## Implemented the Signup page
Added below line of codes to the signup.js file
    import { Auth } from 'aws-amplify';

    const onsubmit = async (event) => {
    event.preventDefault();
    setErrors('')
    try {
      const { user } = await Auth.signUp({
        username: email,
        password: password,
        attributes: {
          name: name,
          email: email,
          preferred_username: username,
        },
        autoSignIn: { // optional - enables auto sign in after user is confirmed
          enabled: true,
        }
      });
      console.log(user);
      window.location.href = `/confirm?email=${email}`
    } catch (error) {
        console.log(error);
        setErrors(error.message)
    }
    return false
  }

## Confirmation Page
    import { Auth } from 'aws-amplify';
    
    const resend_code = async (event) => {
    setErrors('')
    try {
      await Auth.resendSignUp(email);
      console.log('code resent successfully');
      setCodeSent(true)
    } catch (err) {
      // does not return a code
      // does cognito always return english
      // for this to be an okay match?
      console.log(err)
      if (err.message == 'Username cannot be empty'){
        setCognitoErrors("You need to provide an email in order to send Resend Activiation Code")   
      } else if (err.message == "Username/client id combination not found."){
        setCognitoErrors("Email is invalid or cannot be found.")   
        }
     }
    }

    const onsubmit = async (event) => {
        event.preventDefault();
        setErrors('')
        try {
        await Auth.confirmSignUp(email, code);
        window.location.href = "/"
        } catch (error) {
        setErrors(error.message)
        }
        return false
    }

## Added Recovery Page
Added below line of code to the RecoverPage.js file
    import { Auth } from 'aws-amplify';

    const onsubmit_send_code = async (event) => {
    event.preventDefault();
    setErrors('')
    Auth.forgotPassword(username)
    .then((data) => setFormState('confirm_code') )
    .catch((err) => setErrors(err.message) );
    return false
  }

    const onsubmit_confirm_code = async (event) => {
    event.preventDefault();
    setErrors('')
    if (password == passwordAgain){
      Auth.forgotPasswordSubmit(username, code, password)
      .then((data) => setFormState('success'))
      .catch((err) => setErrors(err.message) );
    } else {
      setErrors('Passwords do not match')
    }
    return false
  }