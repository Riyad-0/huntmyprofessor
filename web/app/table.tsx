'use client'
import { ChangeEventHandler, useState } from 'react';
import { FaSort, FaSortDown, FaSortUp } from 'react-icons/fa';
import { LuChevronDown, LuChevronsUpDown, LuChevronUp } from 'react-icons/lu';
import { ComboboxWithClear } from './combobox';
import { Input } from '@/components/ui/input';

function randomProfessorRow() {
  return [
    randomFullName(),
    randomPercent(),
    randomPercent(),
    randomResponseCount(),
  ];
}

function professorRow(i: number) {
  return [
    'QOGLGQIAIJNPEPXAZ, YBCZTRYZF',
    i + 1,
    i + 1,
    i + 1,
  ]
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

function into_row(professor) {
  
}

export default function Table({ rows }: { rows: any[] }) {
  // const cookieStore = await cookies()
  // const supabase = createClient(cookieStore)
  const [searchValue, setSearchValue] = useState('');
  const [[sortBy, sortOrder], setSort] = useState<[string, SortOrder]>(['Rating', 1]);

  const courses = [{

  }]

  // const { data: courses } = await supabase.from('course').select()
  // console.log(courses)
  const headers = [
    new_header('Rank', 'number', false),
    new_header('Professor', 'text', false),
    new_header('Rating', 'number', true),
    new_header("A's", 'number', true),
    new_header('Responses', 'number', true),
    new_header('Recent courses', 'text', false),
  ];

  function searchText(source: string, arg: string) {
    return source.split(/\s+/).some(substr => substr.toLowerCase().includes(arg.toLowerCase()));
  }

  const filteredRows = searchValue.trim() === '' ? rows : rows.filter(row => {
    return row.some(value => {
      if (Array.isArray(value)) {
        return value.some(x => searchText(x, searchValue));
      } else if (typeof value === 'string') {
        return searchText(value, searchValue);
      } else {
        return false;
      }
    });
  });
  
  const tableRows = filteredRows.toSorted((a, b) => {
    const wip_i = headers.findIndex(h => h.name == sortBy);
    console.log(wip_i, sortBy);
    if (wip_i === -1) return;
    const i = wip_i - 1
    return (b[i] - a[i]) * sortOrder;
  });
  console.log(sortBy);

  const onSearchChange: ChangeEventHandler<HTMLInputElement, HTMLInputElement> = e => {
    setSearchValue(e.target.value);
  }

  return (
    <>
      {/* <select className='dark:bg-gray-700 rounded-lg w-40 h-8 ml-16 mt-16'>
        <option>test</option>
        <option>test2</option>
      </select> */}
      <div className='flex flex-col items-center mt-20'>
        <Input value={searchValue} onChange={onSearchChange} className='w-80' placeholder='Search' />
        <table className='dark:text-white mt-16'>
          <thead className=''>
            <tr className='sticky top-0 bg-[background] border-b border-solid border-gray-300 dark:border-gray-700'>
              {headers.map(({ name, kind, sortable }) => {
                // <FaSort />
                // <FaSortUp />
                // <FaSortDown />
                function sort() {
                  if (sortBy === name) {
                    console.log(name, sortBy, sortOrder);
                    setSort([name, -sortOrder as SortOrder]);
                  } else {
                    setSort([name, 1]);
                  }
                }
                const colSortOrder = name === sortBy ? sortOrder : 0;
              
                const inner = sortable ?
                  <button onClick={sort} className='px-4 py-2 flex gap-x-1 w-full items-center justify-start hover:bg-gray-100 dark:hover:bg-gray-800'>
                    <SortIcon sortOrder={colSortOrder} />
                    <div>{name}</div>
                  </button> :
                  <div className='px-4 py-2'>{name}</div>;
                // const inner = (<button className='flex items-center dark:hover:bg-gray-800'><div>{name}</div>{sortOption}</button>)
                return (
                  kind == 'number' ?
                    <th className='text-end' key={name}>{inner}</th> :
                    <th className='text-start' key={name}>{inner}</th>
                );
              })}
            </tr>
          </thead>
          <tbody className='dark:text-gray-200'>
            {tableRows.map((row, i) => (
              <tr className='border-b border-solid border-gray-300 dark:border-gray-700 align-top'>
                {[i+1, ...row].map((value, j) => {
                  const kind = headers[j].kind;
                  return (<Cell value={value} kind={kind} />);
                  // return (
                  //   kind == 'number' ?
                  //     <td className='text-end px-4 py-2'>{value}</td> :
                  //     <td className='text-start px-4 py-2'>{value}</td>
                  // );
                })}
              </tr>
            ))}
          </tbody>
        </table>
      
      </div>
    </>
    // <ul className='dark:text-white'>
    //   {courses?.map((course) => (
    //     <li key={course.id}>{course.name}</li>
    //   ))}
    // </ul>
  )
}

function Cell({ value, kind }: { value: any, kind: string }) {
  return (
    kind == 'number' ?
      <td className='text-end px-4 py-2'><CellInner value={value}></CellInner></td> :
      <td className='text-start px-4 py-2'><CellInner value={value}></CellInner></td>
  );
}

function CellInner({ value }: { value: any }) {
  if (Array.isArray(value)) {
    return (
    <div className='flex flex-col'>
      {value.map(x => <div key={x}>{x}</div>)}
    </div>
    );
  } else {
    return (<div>{value}</div>);
  }
}

type SortOrder = 1 | -1 | 0;

function SortIcon({ sortOrder }: { sortOrder: SortOrder }) {
  switch (sortOrder) {
     case -1: return <LuChevronDown className='dark:text-gray-300' />
     case 1: return <LuChevronUp className='dark:text-gray-300' />
     case 0: return <LuChevronsUpDown className='dark:text-gray-300' />
  }
}