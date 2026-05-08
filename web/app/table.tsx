// @ts-nocheck
'use client'
import { ChangeEventHandler, JSX, useState } from 'react';
import { FaSort, FaSortDown, FaSortUp } from 'react-icons/fa';
import { LuChevronDown, LuChevronsUpDown, LuChevronUp } from 'react-icons/lu';
import { ComboboxWithClear } from './combobox';
import { Input } from '@/components/ui/input';
import { DbProfessor } from './db_professor';

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

class Header {
  constructor(
    public readonly name: string,
    public readonly kind: string,
    public readonly sortable: boolean,
  ) {}
}

function intoRow(rank: number, professor: DbProfessor) {
  return [
    rank,
    formatName(professor.name),
    Math.round((professor.rating - 1) / 6 * 100),
    Math.round(professor.a_count / professor.response_count * 100),
    professor.response_count,
    professor.recent_courses,
  ];
}

// type Header =
//  | 'Rank'
//  | 'Professor'
//  | 'Rating'
//  | "A's"
//  | 'Responses'
//  | 'Recent courses';

function abbreviate(value: any): any {
  if (typeof value != 'string') {
    return value;
  }
  switch (value) {
    // case 'Professor': return 'Prof.';
    case 'Rank': return 'Rk';
    case 'Rating': return 'Rat.';
    case 'Responses': return 'n';
    case 'Recent courses': return 'Cour.';
    default: {
      return value;
      // if (value.includes('-')) return value;
      // const split = value.split(' ').map(x => {
      //   const l = 10;
      //   if (x.length > l) {
      //     return x.slice(0, l) + '-\n' + x.slice(l);
      //   } else {
      //     return x;
      //   }
      // });
      // return split.join(' ');
    }
  }
}

export default function Table({ professors }: { professors: DbProfessor[] }) {
  // const cookieStore = await cookies()
  // const supabase = createClient(cookieStore)
  // const fakeProfessor = {
  //   name: 'SHOKRI, MOHAMMADMAHDI',
  //   rating: 6,
  //   a_count: 120,
  //   response_count: 201,
  //   recent_courses: ['CSCI 12000']
  // };
  // professors = [];
  // for (let i = 0; i < 80; i++) {
  //   professors.push({
  //     id: i,
  //     ...fakeProfessor
  //   });
  // }
  const [searchValue, setSearchValue] = useState('');
  const [[sortBy, sortOrder], setSort] = useState<[string, SortOrder]>(['Rating', -1]);

  const courses = [{

  }]

  // const { data: courses } = await supabase.from('course').select()
  // console.log(courses)
  const headers = [
    new Header('Rank', 'number', false),
    new Header('Professor', 'text', false),
    new Header('Rating', 'percent', true),
    new Header("A's", 'percent', true),
    new Header('Responses', 'number', true),
    new Header('Recent courses', 'text', false),
  ];

  function searchText(source: string, arg: string) {
    if (arg.trim().length === 0) {
      return true;
    }
    // const sourceSplit = source.split(/\s+/);
    const orOps = arg.split(',').map(x => x.trim()).filter(x => x.length > 0);
    return orOps.some(orOp => {
      const andOps = orOp.split(/\s+/).filter(x => x.length > 0);
      return andOps.every(argPiece => source.toLowerCase().includes(argPiece.toLowerCase()));
    });
    // const argSplit = arg.split(/\s+/).filter(s => s.length > 0);
    // if (argSplit.length === 0) {
    //   return true;
    // }
    // return argSplit.every(argPiece => source.toLowerCase().includes(argPiece.toLowerCase()));
    // return source.split(/\s+/).some(substr => substr.toLowerCase().includes(arg.toLowerCase()));
  }

  const filtered = searchValue.trim() === '' ? professors : professors.filter(professor => {
    return Object.values(professor).some(value => {
      if (Array.isArray(value)) {
        return value.some(x => searchText(x, searchValue));
      } else if (typeof value === 'string') {
        return searchText(value, searchValue);
      } else {
        return false;
      }
    });
  });
  const sorted = filtered.map((p, i) => intoRow(i+1, p)).toSorted((a: T, b: T) => {
    const wip_i = headers.findIndex(h => h.name == sortBy);
    if (wip_i === -1) return;
    const i = wip_i;
    return (a[i] - b[i]) * sortOrder;
  });

  // const filteredRows = searchValue.trim() === '' ? rows : rows.filter(row => {
  //   return row.some(value => {
  //     if (Array.isArray(value)) {
  //       return value.some(x => searchText(x, searchValue));
  //     } else if (typeof value === 'string') {
  //       return searchText(value, searchValue);
  //     } else {
  //       return false;
  //     }
  //   });
  // });
  
  // const tableRows = filteredRows.toSorted((a, b) => {
  //   const wip_i = headers.findIndex(h => h.name == sortBy);
  //   console.log(wip_i, sortBy);
  //   if (wip_i === -1) return;
  //   const i = wip_i - 1
  //   return (b[i] - a[i]) * sortOrder;
  // });
  // console.log(sortBy);

  const onSearchChange: ChangeEventHandler<HTMLInputElement, HTMLInputElement> = e => {
    setSearchValue(e.target.value);
  }

  return (
    <>
      {/* <select className='dark:bg-gray-700 rounded-lg w-40 h-8 ml-16 mt-16'>
        <option>test</option>
        <option>test2</option>
      </select> */}
      <div className='flex flex-col items-center sm:items-center'>
        <div className='px-1 w-80 max-w-full mt-20'>
          <Input value={searchValue} onChange={onSearchChange} className='' placeholder='Search' />
        </div>
        <div className='overflow-x-auto max-w-full'>
          <table className='mt-16 text-sm sm:text-base'>
            <thead className=''>
              <tr className='sticky top-0 bg-[background] border-b border-solid border-gray-300'>
                {headers.map(({ name, kind, sortable }) => {
                  return (<Th key={name} name={name} kind={kind} sortable={sortable} sortBy={sortBy} sortOrder={sortOrder} setSort={setSort} />);
                  // <FaSort />
                  // <FaSortUp />
                  // <FaSortDown />
                  // function sort() {
                  //   if (sortBy === name) {
                  //     setSort([name, invert(sortOrder)]);
                  //   } else {
                  //     setSort([name, -1]);
                  //   }
                  // }
                  // const colSortOrder = name === sortBy ? sortOrder : 0;
                  // // const abbrev = abbreviate(name);
                
                  // const inner = sortable ?
                  //   <button onClick={sort} className='sm:px-2 px-0.5 sm:py-2 py-1 flex sm:gap-x-1 w-full items-end justify-start hover:bg-gray-100'>
                  //     <SortIcon sortOrder={colSortOrder} />
                  //     <div className='hidden sm:block'>{name}</div>
                  //     <div className='sm:hidden'>{abbreviate(name)}</div>
                  //   </button> :
                  //   <div className='sm:px-2 px-0.5 sm:py-2 py-1'>
                  //     <div className='hidden sm:block'>{name}</div>
                  //     <div className='sm:hidden'>{abbreviate(name)}</div>
                  //   </div>;
                  // // const inner = (<button className='flex items-center dark:hover:bg-gray-800'><div>{name}</div>{sortOption}</button>)
                  // return (
                  //   kind === 'number' || kind === 'percent' ?
                  //     <th className='text-end align-bottom' key={name}>{inner}</th> :
                  //     <th className='text-start align-bottom' key={name}>{inner}</th>
                  // );
                })}
              </tr>
            </thead>
            <tbody className=''>
              {sorted.map((row, i) => (
                <tr key={row[1]} className='border-b border-solid border-gray-300 align-top'>
                  {row.map((value, j) => {
                    if (j === 0) {
                      value = i + 1;
                    }
                    const kind = headers[j].kind;
                    return (<Cell key={headers[j].name} value={value} kind={kind} />);
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
      </div>
    </>
    // <ul className=''>
    //   {courses?.map((course) => (
    //     <li key={course.id}>{course.name}</li>
    //   ))}
    // </ul>
  )
}

function formatName(name: string): string {
  // const specialCase = formatNameSpecialCase(name);
  // if (specialCase !== null) {
  //   return specialCase;
  // }
  const [last, firstAndMiddle] = name.split(", ");
  const wipSplit = firstAndMiddle.split(' ').map((x, i) => {
    if (i > 0 && x.length === 1) {
      return x + '.';
    } else {
      return x;
    }
  });
  wipSplit.push(...last.split(' '));
  // const wipName = firstAndMiddle + ' ' + last;
  // const split = wipName.split(' ');
  const split = wipSplit;
  return split.map(s => {
    return s.split('-').map(toTitleCase).join('-');
  }).join(' ');
}

// function formatNameSpecialCase(name: string): string | null {
//   switch (name) {
//     case 'ELSAYED, ALI': return 'Ali ElSayed';
//     default: return null;
//   }
// }
function toTitleCase(name: string): string {
  if (name.length === 0) {
    return '';
  }
  return name[0].toUpperCase() + name.slice(1).toLowerCase();
}

function Th({ name, kind, sortable, sortBy, sortOrder, setSort }: {
  name: string,
  kind: string,
  sortable: boolean,
  sortBy: string,
  sortOrder: SortOrder,
  setSort: (_: [name: string, order: SortOrder]) => void,
}) {
  // function sort() {
  //   if (sortBy === name) {
  //     setSort([name, invert(sortOrder)]);
  //   } else {
  //     setSort([name, -1]);
  //   }
  // }
  // const colSortOrder = name === sortBy ? sortOrder : 0;
  // const abbrev = abbreviate(name);

  // const inner = sortable ?
  //   <button onClick={sort} className='sm:px-2 px-0.5 sm:py-2 py-1 flex sm:gap-x-1 w-full items-end justify-start hover:bg-gray-100'>
  //     <SortIcon sortOrder={colSortOrder} />
  //     <div className='hidden sm:block'>{name}</div>
  //     <div className='sm:hidden'>{abbreviate(name)}</div>
  //   </button> :
  //   <div className='sm:px-2 px-0.5 sm:py-2 py-1'>
  //     <div className='hidden sm:block'>{name}</div>
  //     <div className='sm:hidden'>{abbreviate(name)}</div>
  //   </div>;
  // const inner = (<button className='flex items-center dark:hover:bg-gray-800'><div>{name}</div>{sortOption}</button>)
  // const textAlign = kind === 'number' || kind === 'percent' ? 'text-end' : 'text-start';
  return (
    kind === 'number' || kind === 'percent' ?
      <NumberTh name={name} kind={kind} sortable={sortable} sortBy={sortBy} sortOrder={sortOrder} setSort={setSort} /> :
      <TextTh name={name} kind={kind} sortable={sortable} sortBy={sortBy} sortOrder={sortOrder} setSort={setSort} />
  );
}

function NumberTh({ name, kind, sortable, sortBy, sortOrder, setSort }: {
  name: string,
  kind: string,
  sortable: boolean,
  sortBy: string,
  sortOrder: SortOrder,
  setSort: (_: [name: string, order: SortOrder]) => void,
}) {
  return (
    <th className='text-end align-bottom'>
      <ThContent name={name} kind={kind} sortable={sortable} sortBy={sortBy} sortOrder={sortOrder} setSort={setSort} />
    </th>
  );
}

function TextTh({ name, kind, sortable, sortBy, sortOrder, setSort }: {
  name: string,
  kind: string,
  sortable: boolean,
  sortBy: string,
  sortOrder: SortOrder,
  setSort: (_: [name: string, order: SortOrder]) => void,
}) {
  return (
    <th className='text-start align-bottom'>
      <ThContent name={name} kind={kind} sortable={sortable} sortBy={sortBy} sortOrder={sortOrder} setSort={setSort} />
    </th>
  );
}

function ThContent({ name, kind, sortable, sortBy, sortOrder, setSort }: {
  name: string,
  kind: string,
  sortable: boolean,
  sortBy: string,
  sortOrder: SortOrder,
  setSort: (_: [name: string, order: SortOrder]) => void,
}) {
  function sort() {
    if (sortBy === name) {
      setSort([name, invert(sortOrder)]);
    } else {
      setSort([name, -1]);
    }
  }

  if (sortable) {
    const colSortOrder = name === sortBy ? sortOrder : 0;  // const abbrev = abbreviate(name);
    return (
      <button onClick={sort} className='sm:px-2 px-0.5 sm:py-2 py-1 flex sm:gap-x-1 w-full items-end justify-start hover:bg-gray-100'>
        <SortIcon sortOrder={colSortOrder} />
        <div className='hidden sm:flex flex-col justify-end'>
          {kind === 'percent' ? <div className='font-normal text-gray-500 text-[0.875em]'>%</div> : <></>}
          <div>{name}</div>
        </div>
        <div className='sm:hidden flex flex-col justify-end'>
          {kind === 'percent' ? <div className='font-normal text-gray-500 text-[0.875em]'>%</div> : <></>}
          <div>{abbreviate(name)}</div>
        </div>
      </button>
    );
  } else {
    return (
      <div className='sm:px-2 px-0.5 sm:py-2 py-1'>
        <div className='hidden sm:block'>{name}</div>
        <div className='sm:hidden'>{abbreviate(name)}</div>
      </div>
    );
  }
}

function Cell({ value, kind }: { value: any, kind: string }) {
  return (
    kind === 'number' || kind === 'percent' ?
      <td className='text-end sm:px-2 px-0.5 sm:py-2 py-1'><CellInner value={value} kind={kind}></CellInner></td> :
      <td className='text-start sm:px-2 px-0.5 sm:py-2 py-1'><CellInner value={value} kind={kind}></CellInner></td>
  );
}

function CellInner({ value, kind }: { value: any, kind: string }) {
  if (Array.isArray(value)) {
    return (
    <div className='flex flex-col'>
      {value.map(x => <div key={x}>{<AllowAbbrev value={x} kind={kind} />}</div>)}
    </div>
    );
  } else {
    return (<div><AllowAbbrev value={value} kind={kind} /></div>);
  }
}

type SortOrder = 1 | -1 | 0;

function invert(sortOrder: SortOrder): SortOrder {
  return -sortOrder as SortOrder;
}

function SortIcon({ sortOrder }: { sortOrder: SortOrder }) {
  switch (sortOrder) {
     case -1: return <LuChevronDown className='mb-[.25em]' />
     case 1: return <LuChevronUp className='mb-[.25em]' />
     case 0: return <LuChevronsUpDown className='mb-[.25em]' />
  }
}

function AllowAbbrev({ value, kind }: { value: any, kind: string }) {
  // if (kind === 'percent') {
  //   value += '%';
  // }
  return (
    <>
      <div className='hidden sm:block'>{value}</div>
      <div className='sm:hidden'>{abbreviate(value)}</div>
    </>
  );
}

// function AllowAbbrev({ value }: { value: any }) {
//   const wipAbbrev = abbreviate(value);
//   let abbrev = wipAbbrev;
//   if (typeof wipAbbrev === 'string') {
//     const split = wipAbbrev.split('\n');
//     const abbrev = split.map((x, i) => {
//       if (i > 0) {
//         return (<><br />{x}</>);
//       } else {
//         return <>{x}</>
//       }
//     });
//   }
//   return (
//     <>
//       <div className='hidden sm:block'>{value}</div>
//       <div className='sm:hidden'>{}</div>
//     </>
//   );
// }

function Abbrev({ value }: { value: any }) {

}