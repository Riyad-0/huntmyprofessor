
import { createClient } from '@/utils/supabase/server'
import { SupabaseClient } from '@supabase/supabase-js'
import { cookies } from 'next/headers'

async function getCourses(supabase: SupabaseClient) {
  const { data: courses } = await supabase.from('course').select().limit(10)
}

export default async function Home() {
  const cookieStore = await cookies()
  const supabase = createClient(cookieStore)

  // const { data: courses } = await supabase.from('course').select()
  // console.log(courses)

  return (
    <div></div>
    // <ul className='dark:text-white'>
    //   {courses?.map((course) => (
    //     <li key={course.id}>{course.name}</li>
    //   ))}
    // </ul>
  )
}