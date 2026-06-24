/* address: 0x004bfab0 */
/* name: OID__Unk_004bfab0 */
/* signature: void __thiscall OID__Unk_004bfab0(void * this, int param_1, int param_2) */


void __thiscall OID__Unk_004bfab0(void *this,int param_1,int param_2)

{
  int iVar1;
  uint unaff_EDI;

  if ((*(int *)((int)this + 0x48) != 0) &&
     (iVar1 = CUnit__Unk_004f6fd0(this,(void *)param_1,unaff_EDI), (char)iVar1 != '\0')) {
    return;
  }
  RenderState_Set(0x1b,0);
  CThing__Render(this,param_1,unaff_EDI);
  RenderState_Set(0x1b,1);
  return;
}
