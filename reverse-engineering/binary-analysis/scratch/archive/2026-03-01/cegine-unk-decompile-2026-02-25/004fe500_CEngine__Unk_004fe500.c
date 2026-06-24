/* address: 0x004fe500 */
/* name: CEngine__Unk_004fe500 */
/* signature: void __thiscall CEngine__Unk_004fe500(void * this, void * param_1, void * param_2) */


void __thiscall CEngine__Unk_004fe500(void *this,void *param_1,void *param_2)

{
  CGenericActiveReader__SetReader((void *)((int)this + 0x148),param_1);
  if (param_1 != (void *)0x0) {
    CSPtrSet__Remove(&DAT_008550c0,this);
    CSPtrSet__Remove(&DAT_008550b0,this);
  }
  return;
}
