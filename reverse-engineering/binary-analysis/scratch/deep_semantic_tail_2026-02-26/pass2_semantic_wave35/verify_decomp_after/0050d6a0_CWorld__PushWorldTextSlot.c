/* address: 0x0050d6a0 */
/* name: CWorld__PushWorldTextSlot */
/* signature: void __thiscall CWorld__PushWorldTextSlot(void * this, int param_1, int param_2, int param_3) */


void __thiscall CWorld__PushWorldTextSlot(void *this,int param_1,int param_2,int param_3)

{
  int *piVar1;
  short *psVar2;
  int iVar3;

  iVar3 = 0;
  piVar1 = (int *)((int)this + 0x20c);
  do {
    if (*piVar1 == 0) {
      psVar2 = CText__GetStringById(&g_Text,param_1);
      *(short **)((int)this + iVar3 * 4 + 0x22c) = psVar2;
      *(int *)((int)this + iVar3 * 4 + 0x21c) = param_1;
      *(int *)((int)this + iVar3 * 4 + 0x20c) = param_2;
      *(undefined4 *)((int)this + iVar3 * 4 + 0x23c) = 0;
      *(undefined4 *)((int)this + iVar3 * 4 + 0x24c) = 0;
      *(undefined4 *)((int)this + iVar3 * 4 + 0x25c) = DAT_00672fd0;
      return;
    }
    iVar3 = iVar3 + 1;
    piVar1 = piVar1 + 1;
  } while (iVar3 < 4);
  return;
}
