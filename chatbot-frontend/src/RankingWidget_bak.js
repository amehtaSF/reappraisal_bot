import React, { useState, useEffect } from 'react';
import { DragDropContext, Droppable, Draggable } from 'react-beautiful-dnd';

function RankingWidget({ onSend, item_dict = {}, isSending }) {
  // Convert item_dict to an array of items with id and content
  const [items, setItems] = useState([]);

  useEffect(() => {
    const initialItems = Object.entries(item_dict).map(([id, content]) => ({
      id: id.toString(), // Ensure id is a string
      content: content,
    }));
    setItems(initialItems);
  }, [item_dict]);

  const onDragEnd = (result) => {
    if (!result.destination) return;

    const reorderedItems = Array.from(items);
    const [movedItem] = reorderedItems.splice(result.source.index, 1);
    reorderedItems.splice(result.destination.index, 0, movedItem);

    setItems(reorderedItems);
  };

  const handleSend = () => {
    // Create a dictionary mapping item ids to their new ranks
    const rankDict = {};
    items.forEach((item, index) => {
      rankDict[item.id] = index + 1; // Ranks start from 1
    });
    onSend(rankDict);
  };

  return (
    <div className="ranking-widget">
      <DragDropContext onDragEnd={onDragEnd}>
        <Droppable droppableId="rankingList">
          {(provided) => (
            <ul
              className="ranking-list"
              {...provided.droppableProps}
              ref={provided.innerRef}
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
                      className={`ranking-item ${snapshot.isDragging ? 'dragging' : ''}`}
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
