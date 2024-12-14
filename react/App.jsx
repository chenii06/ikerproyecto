
import Modal from 'react-modal';
import Example from './example';

function App({listRoulette, newLevel, setRender, roulette, modalIsOpen, setModalIsOpen}) {
  
  return (
    <div className="App">
      <button className='roulette-button' onClick={() => setModalIsOpen(true)}>Next level</button>
      <Modal 
        isOpen={modalIsOpen}
       
        style={{
          overlay: {
            backgroundColor: 'rgba(0, 0, 0, 0.144)'
          },
          content: {
            display: 'flex',
            justifyContent: 'center',
            alignItems: 'center',
            color: 'lightsteelblue',
            width: '80%', 
            margin: '0 auto', 
            background: '#14141A',
            border: 'solid 1px #282834'
          }
        }}
        contentLabel="Example Modal"
      >
        <Example
          setModalIsOpen={setModalIsOpen}
          listRoulette={listRoulette}
          newLevel={newLevel}
          roulette={roulette}
          setRender={setRender} />
      </Modal>
     
    </div>
  );
}

export default App;