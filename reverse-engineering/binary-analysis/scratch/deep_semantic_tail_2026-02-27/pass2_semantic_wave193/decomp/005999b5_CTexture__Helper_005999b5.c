/* address: 0x005999b5 */
/* name: CTexture__Helper_005999b5 */
/* signature: void __fastcall CTexture__Helper_005999b5(void * param_1) */


void __fastcall CTexture__Helper_005999b5(void *param_1)

{
  *(undefined ***)param_1 = &PTR_CTexture__NodeType12_ScalarDeletingDtor_005ef384;
  if (*(undefined4 **)((int)param_1 + 0x28) != (undefined4 *)0x0) {
    (**(code **)**(undefined4 **)((int)param_1 + 0x28))(1);
  }
  CDXTexture__ReleaseNodePayloadChain(param_1);
  return;
}
