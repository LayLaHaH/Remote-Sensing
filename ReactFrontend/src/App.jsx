import { useState } from 'react'
import reactLogo from './assets/react.svg'
import './App.css'
import {IconHome,IconAddOutline,IconSatellite,IconSend,IconRobot,IconUserSecret,IconBookmark,IconRocketLaunch,IconMessage} from './SVG';
import ChatBot from 'react-simple-chatbot'
import { height, width } from '@fortawesome/free-regular-svg-icons/faAddressBook';

// const steps = [
//   {
//     id: '1',
//     message: 'What is your name?',
//     trigger: '2',
//   },
//   {
//     id: '2',
//     user: true,
//     trigger: '3',
//   },
//   {
//     id: '3',
//     message: 'Hi {previousValue}, nice to meet you!',
//     end: true,
//   },
// ];

const App = () => (
  
  // <ChatBot 
  // // headerTitle="Speech Recognition"
  // // recognitionEnable={true}
  // steps={steps} />
  
  <div className="App">
    <div className="sideBar">
      <div className="upperSide">
        <div className="upperSideTop">
          <span className="brand"> 
            <IconSatellite className="icon_s" style={{ color: 'white' ,height:'50px' ,width:'50px',}} />Remote sensing chat
          </span>
        </div>
        <button className="midBtn">
          <IconAddOutline className="icon" style={{ color: 'white' ,height:'20px' ,width:'20px'}} /> New Chat
        </button>
        <div className="upperSideBottom">
          <button className="query"><IconMessage className="icon" style={{ color: 'white' ,height:'20px' ,width:'20px'}} />
            Lord of the rings movie ? </button>
          <button className="query"><IconMessage className="icon" style={{ color: 'white' ,height:'20px' ,width:'20px'}} />
            attack on titan anime ? </button>
        </div>
      </div>

      <div className="lowerSide">
        <div className="listItems"><IconHome className="icon" style={{ color: 'white' }} />  
          Home</div>
        <div className="listItems"><IconBookmark className="icon" style={{ color: 'white' }} />  
          Saved</div>
        <div className="listItems"><IconRocketLaunch className="icon" style={{ color: 'white' }} />  
          Upgrade To Pro</div>

      </div>

    </div>
    <div className="main">
      <div className="chats">
        <div className="chat">
          <IconRobot className="icon_u" style={{ color: 'white',height:'50px' ,width:'50px' }}/>
          <p className="txt">Lorem ipsum dolor sit amet consectetur adipisicing elit. Incidunt atque aperiam optio sequi debitis. Totam, perspiciatis doloribus aliquid ut rerum aliquam animi nobis maiores dignissimos nihil dicta suscipit autem voluptates!</p>
        </div>
        <div className="chat bot">
          <IconUserSecret className="icon_u" style={{ color: 'white',height:'50px' ,width:'50px' }}/>
          <p className="txt">Lorem ipsum, dolor sit amet consectetur adipisicing elit. Error minima autem quos et, sint itaque, aspernatur quae animi delectus ullam nihil! Nam voluptatum obcaecati dolor autem dolorem, officiis quam deleniti soluta ea necessitatibus eius dolores voluptatem, modi similique corporis cum eum, itaque aliquid? Ab quas repudiandae sed voluptatum temporibus vel aperiam officia exercitationem! Esse voluptas eaque doloribus iusto adipisci distinctio facilis earum ad cum, dolorem at saepe architecto assumenda nostrum corporis reprehenderit voluptatibus autem quidem suscipit debitis nulla numquam sit. Corrupti illo facere consequuntur necessitatibus nostrum cum natus. Ducimus, aut natus possimus cupiditate vel qui quisquam soluta facere. Aliquid, earLorem ipsum, dolor sit amet consectetur adipisicing elit. Error minima autem quos et, sint itaque, aspernatur quae animi delectus ullam nihil! Nam voluptatum obcaecati dolor autem dolorem, officiis quam deleniti soluta ea necessitatibus eius dolores voluptatem, modi similique corporis cum eum, itaque aliquid? Ab quas repudiandae sed voluptatum temporibus vel aperiam officia exercitationem! Esse voluptas eaque doloribus iusto adipisci distinctio facilis earum ad cum, dolorem at saepe architecto assumenda nostrum corporis reprehenderit voluptatibus autem quidem suscipit debitis nulla numquam sit. Corrupti illo facere consequuntur necessitatibus nostrum cum natus. Ducimus, aut natus possimus cupiditate vel qui quisquam soluta facere. Aliquid, earLorem ipsum, dolor sit amet consectetur adipisicing elit. Error minima autem quos et, sint itaque, aspernatur quae animi delectus ullam nihil! Nam voluptatum obcaecati dolor autem dolorem, officiis quam deleniti soluta ea necessitatibus eius dolores voluptatem, modi similique corporis cum eum, itaque aliquid? Ab quas repudiandae sed voluptatum temporibus vel aperiam officia exercitationem! Esse voluptas eaque doloribus iusto adipisci distinctio facilis earum ad cum, dolorem at saepe architecto assumenda nostrum corporis reprehenderit voluptatibus autem quidem suscipit debitis nulla numquam sit. Corrupti illo facere consequuntur necessitatibus nostrum cum natus. Ducimus, aut natus possimus cupiditate vel qui quisquam soluta facere. Aliquid, earLorem ipsum, dolor sit amet consectetur adipisicing elit. Error minima autem quos et, sint itaque, aspernatur quae animi delectus ullam nihil! Nam voluptatum obcaecati dolor autem dolorem, officiis quam deleniti soluta ea necessitatibus eius dolores voluptatem, modi similique corporis cum eum, itaque aliquid? Ab quas repudiandae sed voluptatum temporibus vel aperiam officia exercitationem! Esse voluptas eaque doloribus iusto adipisci distinctio facilis earum ad cum, dolorem at saepe architecto assumenda nostrum corporis reprehenderit voluptatibus autem quidem suscipit debitis nulla numquam sit. Corrupti illo facere consequuntur necessitatibus nostrum cum natus. Ducimus, aut natus possimus cupiditate vel qui quisquam soluta facere. Aliquid, earum.</p>
        </div>
      </div>
      <div className="chatFooter">
        <div className="inp">
          <input type="text" name="" id="" placeholder='Send a message'/>
          <button className="send"><IconSend className="icon" style={{ color: 'Grey',height:'20px' ,width:'20px' }}/></button>
        </div>
      </div>
    </div>
  </div>
);

export default App;

