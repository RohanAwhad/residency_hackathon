import React, { useState, useRef, useEffect } from 'react';
import { Markmap } from 'markmap-view';
import { transformer } from '@/constants';
import { Toolbar } from 'markmap-toolbar';
import 'markmap-toolbar/dist/style.css';

function renderToolbar(mm, wrapper) {
  while (wrapper?.firstChild) wrapper.firstChild.remove();
  if (mm && wrapper) {
    const toolbar = new Toolbar();
    toolbar.attach(mm);
    // Register custom buttons
    toolbar.register({
      id: 'alert',
      title: 'Click to show an alert',
      content: 'Alert',
      onClick: () => alert('You made it!'),
    });
    toolbar.setItems([...Toolbar.defaultItems, 'alert']);
    wrapper.append(toolbar.render());
  }
}

const GraphTab = (props) => {
  const refSvg = useRef(null)
  const refMm = useRef(null)
  const refToolbar = useRef(null)


  useEffect(() => {
    // Create markmap and save to refMm
    const mmOptions = {
      maxWidth: 300,
      initialExpandLevel: 3,
    }
    if (refMm.current) return;
    const mm = Markmap.create(refSvg.current, mmOptions);
    console.log('create', refSvg.current);
    refMm.current = mm;
    renderToolbar(refMm.current, refToolbar.current);
  }, [refSvg.current]);

  useEffect(() => {
    // Update data for markmap once value is changed
    const mm = refMm.current;
    if (!mm) return;
    const { root } = transformer.transform(props.markdown);
    mm.setData(root);
    mm.fit();
  }, [refMm.current, props.markdown]);

  return (
    <>
      <svg className="flex-1 h-screen w-screen" ref={refSvg} />
      <div className="absolute bottom-1 right-1" ref={refToolbar}></div>
    </>
  )
}

export default GraphTab
