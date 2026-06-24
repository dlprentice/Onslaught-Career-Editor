/* address: 0x004ffdd0 */
/* name: CEngine__Unk_004ffdd0 */
/* signature: void __thiscall CEngine__Unk_004ffdd0(void * this, int param_1, void * param_2, int param_3) */


void __thiscall CEngine__Unk_004ffdd0(void *this,int param_1,void *param_2,int param_3)

{
  int unaff_EDI;

  CGenericActiveReader__SetReader((void *)((int)this + 0xc),(void *)param_1);
  CUnit__Unk_004fb840(*(void **)((int)this + 8),(void *)param_1,unaff_EDI);
  *(void **)((int)this + 0x10) = param_2;
  return;
}
