/* address: 0x004e9570 */
/* name: CSquadNormal__SetFactionAndRefreshGlobalLists */
/* signature: void __thiscall CSquadNormal__SetFactionAndRefreshGlobalLists(void * this, void * param_1, int param_2) */


void __thiscall CSquadNormal__SetFactionAndRefreshGlobalLists(void *this,void *param_1,int param_2)

{
  undefined4 *puVar1;
  undefined4 *puVar2;
  int unaff_EDI;

  *(void **)((int)this + 0x7c) = param_1;
  puVar1 = *(undefined4 **)((int)this + 0xa4);
  if (puVar1 == (undefined4 *)0x0) {
    puVar2 = (undefined4 *)0x0;
  }
  else {
    puVar2 = (undefined4 *)*puVar1;
  }
  while (puVar2 != (undefined4 *)0x0) {
    if ((void *)*puVar2 != (void *)0x0) {
      CUnit__Unk_004fd830((void *)*puVar2,param_1,unaff_EDI);
    }
    puVar1 = (undefined4 *)puVar1[1];
    if (puVar1 == (undefined4 *)0x0) {
      puVar2 = (undefined4 *)0x0;
    }
    else {
      puVar2 = (undefined4 *)*puVar1;
    }
  }
  CSPtrSet__Remove(&DAT_008550c0,this);
  CSPtrSet__Remove(&DAT_008550b0,this);
  if ((*(int *)((int)this + 0x7c) == 1) || (*(int *)((int)this + 0x7c) == 6)) {
    CSPtrSet__AddToTail(&DAT_008550c0,this);
  }
  if ((*(int *)((int)this + 0x7c) == 0) || (*(int *)((int)this + 0x7c) == 6)) {
    CSPtrSet__AddToTail(&DAT_008550b0,this);
  }
  return;
}
