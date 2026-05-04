
import { createClient } from '@/utils/supabase/server'
import { SupabaseClient } from '@supabase/supabase-js'
import { cookies } from 'next/headers'
import { FaSort, FaSortDown, FaSortUp } from 'react-icons/fa';

async function getCourses(supabase: SupabaseClient) {
  const { data: courses } = await supabase.from('course').select().limit(10)
}

function randomProfessorRow() {
  return [
    randomFullName(),
    randomPercent(),
    randomPercent(),
    randomResponseCount(),
  ];
}

function randomCourse() {
  return 'CSCI ' + Math.floor(10000 + Math.random() * 70000);
}

function randomFullName() {
  return randomName() + ', ' + randomName();
}

function randomName() {
  const n = 2 + Math.floor(Math.random() * 19);
  let s = '';
  for (let i = 0; i < n; i++) {
    s += String.fromCharCode(65 + Math.floor(Math.random() * 26));
  }
  return s;
}

function randomPercent() {
  return Math.floor(Math.random() * 101);
}

function randomResponseCount() {
  if (Math.random() < 0.9) {
    return 1 + Math.floor(Math.random() * 40);
  } else {
    return 1 + Math.floor(Math.random() * 400);
  }
}

interface Header {

}

function new_header(name: string, kind: string, sortable: boolean) {
  return { name, kind, sortable };
}

export default async function Home() {
  // const cookieStore = await cookies()
  // const supabase = createClient(cookieStore)

  const courses = [{

  }]

  // const { data: courses } = await supabase.from('course').select()
  // console.log(courses)
  const headers = [
    new_header('Rank', 'number', false),
    new_header('Professor', 'text', false),
    new_header('Rating', 'number', true),
    new_header("A's", 'number', true),
    new_header('Responses', 'number', false),
  ];
  const rows = [];
  for (let i = 0; i < 20; i++) {
    rows.push(randomProfessorRow());
  }

  return (
    <div className='flex justify-center mt-32'>
        <table className='dark:text-white w-3xl'>
        <thead>
          <tr className='border-b border-solid border-gray-400 dark:border-gray-700'>
            {headers.map(({ name, kind, sortable }) => {
              <FaSort />
              <FaSortUp />
              <FaSortDown />
              return (
                kind == 'number' ?
                  <th className='text-end p-2' key={name}>{name}</th> :
                  <th className='text-start p-2' key={name}>{name}</th>
              );
            })}
          </tr>
        </thead>
        <tbody>
          {rows.map((row, i) => (
            <tr className='border-b border-solid border-gray-400 dark:border-gray-700'>
              {[i+1, ...row].map((value, j) => {
                const kind = headers[j].kind;
                return (
                  kind == 'number' ?
                    <td className='text-end p-2'>{value}</td> :
                    <td className='text-start p-2'>{value}</td>
                );
              })}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
    // <ul className='dark:text-white'>
    //   {courses?.map((course) => (
    //     <li key={course.id}>{course.name}</li>
    //   ))}
    // </ul>
  )
}