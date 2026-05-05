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

function formatName(name: string): string {
  const [last, firstAndMiddle] = name.split(", ");
  const split = firstAndMiddle.split(' ');
  split.push(last);
  return split.map(s => toTitleCase(s.trim())).join(' ');
}

function toTitleCase(name: string): string {
  if (name.length === 0) {
    return '';
  }
  return name[0].toUpperCase() + name.slice(1).toLowerCase();
}

interface DbProfessor {
  id: number;
  name: string;
  rating: number;
  a_count: number;
  response_count: number;
  recent_courses: string[];
}

export default async function Home() {
  const cookieStore = await cookies();
  const supabase = createClient(cookieStore);
  const wipProfessors = (await getProfessors(supabase)).data;
  const rows = wipProfessors === null ?
    [] :
    wipProfessors.map(professor => [
      formatName(professor.name),
      Math.round((professor.rating - 1) / 6 * 100),
      Math.round(professor.a_count / professor.response_count * 100),
      professor.response_count,
      professor.recent_courses,
    ]);

  return (
    <Table rows={rows} />
  );
}