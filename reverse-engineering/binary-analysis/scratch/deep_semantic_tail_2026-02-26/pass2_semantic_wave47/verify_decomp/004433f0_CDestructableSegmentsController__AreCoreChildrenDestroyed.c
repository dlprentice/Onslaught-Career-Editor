/* address: 0x004433f0 */
/* name: CDestructableSegmentsController__AreCoreChildrenDestroyed */
/* signature: int __fastcall CDestructableSegmentsController__AreCoreChildrenDestroyed(int param_1) */


int __fastcall CDestructableSegmentsController__AreCoreChildrenDestroyed(int param_1)

{
  int iVar1;
  int *piVar2;
  undefined4 *puVar3;

  if (*(int *)(param_1 + 0x30) == 0) {
    CConsole__Printf(&DAT_0066f580,s_Warning__First_core_part_has_no_c_006285bc);
  }
  else {
    puVar3 = *(undefined4 **)(param_1 + 0x24);
    if (puVar3 == (undefined4 *)0x0) {
      piVar2 = (int *)0x0;
    }
    else {
      piVar2 = (int *)*puVar3;
    }
    if (piVar2 != (int *)0x0) {
      do {
        iVar1 = (**(code **)(*piVar2 + 0x14))();
        if ((iVar1 == 0) && (piVar2[0xe] == 0)) {
          return 0;
        }
        puVar3 = (undefined4 *)puVar3[1];
        if (puVar3 == (undefined4 *)0x0) {
          piVar2 = (int *)0x0;
        }
        else {
          piVar2 = (int *)*puVar3;
        }
      } while (piVar2 != (int *)0x0);
      return 1;
    }
  }
  return 1;
}
