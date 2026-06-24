/* address: 0x0051ff90 */
/* name: CFEPVirtualKeyboard__Init */
/* signature: int __fastcall CFEPVirtualKeyboard__Init(void * this) */


int __fastcall CFEPVirtualKeyboard__Init(void *this)

{
  *(undefined4 *)((int)this + 0x6f4) = 0x3f000000;
  *(undefined4 *)((int)this + 0x4c) = 0;
  *(undefined4 *)((int)this + 0x50) = 0;
  *(undefined4 *)((int)this + 0x44) = 0;
  *(undefined4 *)((int)this + 0x6e4) = 0;
  *(undefined4 *)((int)this + 0x6e8) = 0;
  *(undefined4 *)((int)this + 0x6ec) = 0;
  *(undefined4 *)((int)this + 0x6f0) = 0;
  CFEPVirtualKeyboard__Unk_00520530((int)this);
  return 1;
}
