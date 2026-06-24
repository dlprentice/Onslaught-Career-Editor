/* address: 0x0056d553 */
/* name: CTexture__Helper_0056d553 */
/* signature: void __cdecl CTexture__Helper_0056d553(void * param_1) */


void __cdecl CTexture__Helper_0056d553(void *param_1)

{
  uint uVar1;

  uVar1 = *(uint *)((int)param_1 + 4);
  *(uint *)((int)param_1 + 4) = uVar1 >> 1 | *(uint *)((int)param_1 + 8) << 0x1f;
  *(uint *)((int)param_1 + 8) = *(uint *)((int)param_1 + 8) >> 1;
  *(uint *)param_1 = *(uint *)param_1 >> 1 | uVar1 << 0x1f;
  return;
}
