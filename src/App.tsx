import { useState } from 'react'

function App() {
  return (
    <>
      <Login />
    </>
  );
}

type Submit = React.SubmitEventHandler<HTMLFormElement>;
type Change = React.ChangeEventHandler<HTMLInputElement, HTMLInputElement>;

function Login() {
  const [username, setUsername] = useState<string>("");
  const [password, setPassword] = useState<string>("");
  const [courses, setCourses] = useState<string[]>();
  const onSubmit: Submit = async e => {
    e.preventDefault();
    const res = await fetch("/api/login", {
      body: JSON.stringify({
        username,
        password
      }),
      headers: {
        "Content-Type": "application/json"
      },
      method: "POST",
    });
    const body = await res.json();
    if (body.result === "success") {
      setCourses(body.courses);
      console.log(body.courses);
    } else {
      console.log(body.result);
    }
  };
  const onChangeUsername: Change = async e => {
    setUsername(e.target.value);
  };
  const onChangePassword: Change = async e => {
    setPassword(e.target.value);
  };
  return (
    <>
      <form onSubmit={onSubmit}>
        <input onChange={onChangeUsername} value={username} />
        <input onChange={onChangePassword} value={password} />
        <button type='submit'>Submit</button>
      </form>
      {courses === undefined ?
        <></> :
        <div>{courses}</div>
      }
    </>
  );
}

export default App;
