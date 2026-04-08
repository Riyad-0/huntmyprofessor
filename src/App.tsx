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
  const [courses, setCourses] = useState<string[] | undefined>();
  const [searchKind, setSearchKind] = useState<string | undefined>(undefined);
  const onSubmit: Submit = async e => {
    e.preventDefault();
    if (searchKind === "professor") {
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
    } else if (searchKind === "course") {
      console.log("HEYO");
      const res = await fetch("/api/courses", {
        body: JSON.stringify({
          username,
          password
        }),
        headers: {
          "Content-Type": "application/json"
        },
        method: "POST",
      });
      // const body = await res.json();
      // if (body.result === "success") {
      //   setOptions(body.options);
      //   console.log(body.options);
      // } else {
      //   console.log(body.result);
      // }
    }
  };
  const onChangeUsername: Change = async e => {
    setUsername(e.target.value);
  };
  const onChangePassword: Change = async e => {
    setPassword(e.target.value);
  };
  const onChangeSearchKind: React.ChangeEventHandler<HTMLSelectElement, HTMLSelectElement> = e => {
    setSearchKind(e.target.value);
  };
  return (
    <>
      <form onSubmit={onSubmit}>
        <input onChange={onChangeUsername} value={username} />
        <input onChange={onChangePassword} value={password} />
        <select value={searchKind} onChange={onChangeSearchKind}>
          <option value="professor">Professor search</option>
          <option value="course">Course search</option>
        </select>
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
