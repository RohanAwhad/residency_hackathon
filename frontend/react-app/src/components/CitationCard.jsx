import { useState } from "react";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"

import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { faAngleUp } from '@fortawesome/free-solid-svg-icons'

export default function CitationCard(props) {

  // vars
  const [isActive, setIsActive] = useState(false);

  // useEffects

  // functions
  const handleCardClick = () => {
    setIsActive(true);
  }

  const setCardInactive = () => {
    setIsActive(false);
  }

  // render
  return (
    <Card className="w-full mb-2" >
      <CardHeader onClick={handleCardClick}>
        <div className="flex justify-between items-center">
          <span className="text-left text-base">{`[${props.id}]`}</span>
          <CardDescription className="text-right text-base">{props.first_author} et. al</CardDescription>
        </div>
        <CardTitle className="text-left text-base mt-2">{props.title}</CardTitle>
      </CardHeader>
      {isActive && (
        <CardContent>
          <div className="text-left">
            <p className="text-base font-medium">Why was this paper cited?</p>
            <p className="text-sm ">{props.why}</p>
          </div>
          <div className="text-left mt-2">
            <p className="text-base font-medium">Whats the contribution of this paper?</p>
            <p className="text-sm ">{props.contribution}</p>
          </div>
          <div className="text-left mt-2">
            <p className="text-base font-medium">What are related works in this paper that could be of interest?</p>
            <p className="text-sm ">{props.related_works}</p>
          </div>
          <div className="closeBar mt-2" onClick={setCardInactive}>
            <FontAwesomeIcon icon={faAngleUp} />
          </div>
        </CardContent>
      )}
    </Card>
  )
}
