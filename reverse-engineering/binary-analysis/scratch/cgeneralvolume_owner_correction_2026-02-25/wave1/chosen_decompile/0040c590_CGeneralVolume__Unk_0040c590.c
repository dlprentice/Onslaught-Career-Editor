/* address: 0x0040c590 */
/* name: CGeneralVolume__Unk_0040c590 */
/* signature: void __fastcall CGeneralVolume__Unk_0040c590(int param_1) */


void __fastcall CGeneralVolume__Unk_0040c590(int param_1)

{
  if (*(int *)(param_1 + 0x260) != 3) {
    CMonitor__Unk_00414610(*(void **)(param_1 + 0x578));
    return;
  }
  CMonitor__Unk_00412520(*(void **)(param_1 + 0x57c));
  return;
}
