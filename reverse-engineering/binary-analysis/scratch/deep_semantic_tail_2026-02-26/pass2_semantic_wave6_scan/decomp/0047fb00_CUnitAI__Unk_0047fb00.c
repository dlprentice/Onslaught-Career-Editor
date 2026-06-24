/* address: 0x0047fb00 */
/* name: CUnitAI__Unk_0047fb00 */
/* signature: void __thiscall CUnitAI__Unk_0047fb00(void * this, void * param_1, int param_2) */


void __thiscall CUnitAI__Unk_0047fb00(void *this,void *param_1,int param_2)

{
  int iVar1;
  int *piVar2;

  iVar1 = 0;
  piVar2 = this;
  do {
    piVar2 = piVar2 + 3;
    if (*piVar2 == 0) {
      *(void **)((int)this + iVar1 * 0xc + 4) = param_1;
      *(undefined4 *)((int)this + iVar1 * 0xc + 8) = DAT_00672fd0;
      *(undefined4 *)((int)this + (iVar1 * 3 + 3) * 4) = 1;
      return;
    }
    iVar1 = iVar1 + 1;
  } while (iVar1 < 2);
  CConsole__Printf(&DAT_0066f580,s_ERROR__Added_too_many_messages_t_0062cc38);
  return;
}
