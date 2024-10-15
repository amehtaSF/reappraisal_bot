// RankingWidget.js
import React, { useState, useEffect } from 'react';
import { DragDropContext, Droppable, Draggable } from 'react-beautiful-dnd';

function RankingWidget({ onSend, itemsList = [], isSending }) {
  const [items, setItems] = useState([]);

  useEffect(() => {
    const initialItems = itemsList.map((item, index) => ({
      id: index.toString(), // Use index as ID and ensure it's a string
      content: item,
    }));
    setItems(initialItems);
  }, [itemsList]);

  const onDragEnd = (result) => {
    if (!result.destination) return;

    const reorderedItems = Array.from(items);
    const [movedItem] = reorderedItems.splice(result.source.index, 1);
    reorderedItems.splice(result.destination.index, 0, movedItem);

    setItems(reorderedItems);
  };

  const handleSend = () => {
    // Return the reordered list of items
    const reorderedList = items.map((item) => item.content);
    onSend(reorderedList);
  };

  return (
    <div className="ranking-widget">
      <DragDropContext onDragEnd={onDragEnd}>
        <Droppable droppableId="rankingList">
          {(provided) => (
            <ul
              className="ranking-list"
              ref={provided.innerRef}
              {...provided.droppableProps}
            >
              {items.map((item, index) => (
                <Draggable
                  key={item.id}
                  draggableId={item.id}
                  index={index}
                  isDragDisabled={isSending}
                >
                  {(provided, snapshot) => (
                    <li
                      className={`ranking-item ${
                        snapshot.isDragging ? 'dragging' : ''
                      }`}
                      ref={provided.innerRef}
                      {...provided.draggableProps}
                      {...provided.dragHandleProps}
                    >
                      <span className="ranking-number">{index + 1}.</span>
                      <span className="ranking-content">{item.content}</span>
                    </li>
                  )}
                </Draggable>
              ))}
              {provided.placeholder}
            </ul>
          )}
        </Droppable>
      </DragDropContext>
      <button onClick={handleSend} disabled={isSending}>
        Send
      </button>
    </div>
  );
}

export default RankingWidget;
