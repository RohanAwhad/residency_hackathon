import React from 'react'
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"

// const Suggestions = (props) => {
//   let ret = []
//   props.suggestions.forEach((suggestion, idx) => {
//     ret.push(
//       <Card key={idx} className="w-full mb-2">
//         <CardContent>
//           <CardDescription>{suggestion.description}</CardDescription>
//         </CardContent>
//       </Card>
//     )
//   })
//   return (
//     <>
//       {ret}
//     </>
//   )
// }

const Suggestions = (props) => {
  const handleClick = (suggestion) => {
    console.log(suggestion)
    props.setUserCurrMsg(suggestion)
  }

  return (
    <>
      {props.suggestions.map((suggestion, idx) => (
        <Card key={idx} className="w-full mb-2" onClick={() => handleClick(suggestion.suggestion)}>
          <CardContent>
            <div className='text-left text-base pt-2 px-2'>Ask: {suggestion.suggestion}</div>
          </CardContent>
        </Card>
      ))}
    </>
  )
}

export default Suggestions