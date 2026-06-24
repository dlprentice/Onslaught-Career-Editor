/* address: 0x00466ab0 */
/* name: CFrontEnd__Unk_00466ab0 */
/* signature: void __thiscall CFrontEnd__Unk_00466ab0(void * this, int param_1, int param_2) */


void __thiscall CFrontEnd__Unk_00466ab0(void *this,int param_1,int param_2)

{
  CFEPOptions__Cleanup();
  CText__CopyFrom(&g_Text,(void *)((param_1 * 3 + 0xbf4) * 0x10 + (int)this));
  return;
}
