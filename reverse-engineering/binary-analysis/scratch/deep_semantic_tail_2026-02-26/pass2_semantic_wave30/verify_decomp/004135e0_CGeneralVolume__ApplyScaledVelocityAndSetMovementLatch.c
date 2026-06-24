/* address: 0x004135e0 */
/* name: CGeneralVolume__ApplyScaledVelocityAndSetMovementLatch */
/* signature: void __fastcall CGeneralVolume__ApplyScaledVelocityAndSetMovementLatch(int param_1) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void __fastcall CGeneralVolume__ApplyScaledVelocityAndSetMovementLatch(int param_1)

{
  float local_10;
  float fStack_c;

  (**(code **)(**(int **)(param_1 + 0x20) + 0x6c))(&local_10);
  local_10 = local_10 * _DAT_005d8cd4;
  if (fStack_c <= _DAT_005d8574) {
    fStack_c = 0.0;
  }
  else {
    fStack_c = fStack_c * _DAT_005d8cd0;
  }
  (**(code **)(**(int **)(param_1 + 0x20) + 0x74))(&stack0xffffffec);
  *(undefined4 *)(*(int *)(param_1 + 0x20) + 0x638) = 1;
  return;
}
