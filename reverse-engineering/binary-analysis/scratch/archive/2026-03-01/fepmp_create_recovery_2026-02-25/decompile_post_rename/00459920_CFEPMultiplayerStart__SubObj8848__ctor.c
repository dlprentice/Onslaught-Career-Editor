/* address: 0x00459920 */
/* name: CFEPMultiplayerStart__SubObj8848__ctor */
/* signature: void * __fastcall CFEPMultiplayerStart__SubObj8848__ctor(void * this) */


void * __fastcall CFEPMultiplayerStart__SubObj8848__ctor(void *this)

{
  int iVar1;
  undefined4 *puVar2;

  *(undefined ***)this = &PTR_CFEPMultiplayerStart__SubObj8848__Init_005db4fc;
  puVar2 = (undefined4 *)((int)this + 4);
  for (iVar1 = 0x32; iVar1 != 0; iVar1 = iVar1 + -1) {
    *puVar2 = 0;
    puVar2 = puVar2 + 1;
  }
  *(undefined4 *)((int)this + 4) = 1;
  *(undefined4 *)((int)this + 8) = 1;
  *(undefined4 *)((int)this + 0xc) = 1;
  *(undefined4 *)((int)this + 0x10) = 1;
  *(undefined4 *)((int)this + 0xcc) = 0x6e;
  *(undefined4 *)((int)this + 0xe4) = 200;
  *(undefined4 *)((int)this + 0xfc) = 0xe7;
  *(undefined4 *)((int)this + 0x114) = 0x137;
  *(undefined4 *)((int)this + 0x345c) = 4;
  puVar2 = (undefined4 *)((int)this + 0xa2c);
  for (iVar1 = 300; iVar1 != 0; iVar1 = iVar1 + -1) {
    *puVar2 = 0;
    puVar2 = puVar2 + 1;
  }
  return this;
}
