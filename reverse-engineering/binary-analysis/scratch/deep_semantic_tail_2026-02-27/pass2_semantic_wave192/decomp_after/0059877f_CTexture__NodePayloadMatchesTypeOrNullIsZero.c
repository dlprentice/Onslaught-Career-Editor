/* address: 0x0059877f */
/* name: CTexture__NodePayloadMatchesTypeOrNullIsZero */
/* signature: uint __stdcall CTexture__NodePayloadMatchesTypeOrNullIsZero(void * param_1, int param_2) */


uint CTexture__NodePayloadMatchesTypeOrNullIsZero(void *param_1,int param_2)

{
  uint uVar1;

  if (param_1 == (void *)0x0) {
    uVar1 = (uint)(param_2 == 0);
  }
  else {
    uVar1 = (**(code **)(*(int *)param_1 + 4))(param_2);
  }
  return uVar1;
}
