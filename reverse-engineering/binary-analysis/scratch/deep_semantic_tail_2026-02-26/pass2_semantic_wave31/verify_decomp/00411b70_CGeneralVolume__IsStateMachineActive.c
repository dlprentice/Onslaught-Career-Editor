/* address: 0x00411b70 */
/* name: CGeneralVolume__IsStateMachineActive */
/* signature: int __fastcall CGeneralVolume__IsStateMachineActive(int param_1) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

int __fastcall CGeneralVolume__IsStateMachineActive(int param_1)

{
  if ((*(int *)(param_1 + 0x2c) == 0) && (*(float *)(param_1 + 0x48) == _DAT_005d856c)) {
    return 0;
  }
  return 1;
}
