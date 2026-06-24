/* address: 0x00423990 */
/* name: CUnitAI__Unk_00423990 */
/* signature: void __fastcall CUnitAI__Unk_00423990(void * param_1) */


void __fastcall CUnitAI__Unk_00423990(void *param_1)

{
  int iVar1;

  iVar1 = *(int *)((int)param_1 + 8);
  *(int *)((int)param_1 + 8) = *(int *)param_1;
  DXMemBuffer__Skip(*(int *)param_1 - iVar1);
  return;
}
