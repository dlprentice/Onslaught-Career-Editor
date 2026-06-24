/* address: 0x00599831 */
/* name: CTexture__Helper_00599831 */
/* signature: void __fastcall CTexture__Helper_00599831(void * param_1) */


void __fastcall CTexture__Helper_00599831(void *param_1)

{
  int iVar1;
  int *piVar2;

  *(undefined ***)param_1 = &PTR_CTexture__NodeType12_Dtor_DeleteOnFlag_005ef374;
  if (*(undefined4 **)((int)param_1 + 0x3c) != (undefined4 *)0x0) {
    (**(code **)**(undefined4 **)((int)param_1 + 0x3c))(1);
  }
  if (*(undefined4 **)((int)param_1 + 0x40) != (undefined4 *)0x0) {
    (**(code **)**(undefined4 **)((int)param_1 + 0x40))(1);
  }
  piVar2 = (int *)((int)param_1 + 0x44);
  iVar1 = 4;
  do {
    if ((undefined4 *)*piVar2 != (undefined4 *)0x0) {
      (*(code *)**(undefined4 **)*piVar2)(1);
    }
    piVar2 = piVar2 + 1;
    iVar1 = iVar1 + -1;
  } while (iVar1 != 0);
  CDXTexture__ReleaseNodePayloadChain(param_1);
  return;
}
