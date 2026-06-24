/* address: 0x0056d525 */
/* name: CTexture__Helper_0056d525 */
/* signature: void __cdecl CTexture__Helper_0056d525(void * param_1) */


void __cdecl CTexture__Helper_0056d525(void *param_1)

{
  uint uVar1;
  uint uVar2;

  uVar1 = *(uint *)param_1;
  uVar2 = *(uint *)((int)param_1 + 4);
  *(uint *)param_1 = uVar1 * 2;
  *(uint *)((int)param_1 + 4) = uVar2 * 2 | uVar1 >> 0x1f;
  *(uint *)((int)param_1 + 8) = *(int *)((int)param_1 + 8) << 1 | uVar2 >> 0x1f;
  return;
}
