import { createClient } from '@/utils/supabase/server'
import { SupabaseClient } from '@supabase/supabase-js'
import { cookies } from 'next/headers'
import { FaSort, FaSortDown, FaSortUp } from 'react-icons/fa';
import Table from './table';

// async function getCourses(supabase: SupabaseClient) {
//   supabase.
//   const { data: courses } = await supabase.from('course').select().limit(10)
// }

async function getProfessors(supabase: SupabaseClient) {
  return await supabase.from('professor_list').select('*');

}

console.log("woohoo");


export default async function Home() {
  const cookieStore = await cookies();
  const supabase = createClient(cookieStore);
  const professors = (await getProfessors(supabase)).data;
  // const rows = professors === null ?
  //   [] :
  //   professors.map(professor => [
  //     formatName(professor.name),
  //     Math.round((professor.rating - 1) / 6 * 100),
  //     Math.round(professor.a_count / professor.response_count * 100),
  //     professor.response_count,
  //     professor.recent_courses,
  //   ]);

  return (
    <Table professors={professors === null ? [] : professors} />
  );
}