/* address: 0x0051b610 */
/* name: CFEPMultiplayerStart__SubObj4034__ResetFlags */
/* signature: void __fastcall CFEPMultiplayerStart__SubObj4034__ResetFlags(void * this) */


void __fastcall CFEPMultiplayerStart__SubObj4034__ResetFlags(void *this)

{
  *(undefined4 *)((int)this + 0xc) = 0;
  DAT_00677614 = 0;
  *(undefined4 *)((int)this + 0x10) = 1;
  if (DAT_0083d448 == 0) {
    DAT_00677614 = 0;
    *(undefined4 *)((int)this + 0xc) = 0;
  }
  return;
}
