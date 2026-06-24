/* address: 0x00488380 */
/* name: CIBuffer__Create */
/* signature: undefined CIBuffer__Create(void) */


int __thiscall CIBuffer__Create(int *param_1,int param_2)

{
  int iVar1;

  iVar1 = OID__AllocObject(param_2 * 2,0x2f,s_C__dev_ONSLAUGHT2_ibuffer_cpp_0062d390,0x36);
  param_1[7] = iVar1;
  param_1[3] = param_2 * 2;
  param_1[4] = 0;
  param_1[5] = 0x65;
  param_1[6] = 1;
  iVar1 = (**(code **)(*param_1 + 4))();
  FatalError_LocalizedStringId(-1 < iVar1,0xd2,7);
  return iVar1;
}
