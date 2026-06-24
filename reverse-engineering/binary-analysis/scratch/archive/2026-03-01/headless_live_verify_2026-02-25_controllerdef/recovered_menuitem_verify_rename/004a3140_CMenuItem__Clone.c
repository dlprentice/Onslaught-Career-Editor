/* address: 0x004a3140 */
/* name: CMenuItem__Clone */
/* signature: undefined CMenuItem__Clone(void) */


undefined4 * __fastcall CMenuItem__Clone(int param_1)

{
  undefined4 *puVar1;

  puVar1 = (undefined4 *)OID__AllocObject(0x1c,0x80,s_C__dev_ONSLAUGHT2_MenuItem_cpp_0062f7d8,0x27);
  if (puVar1 != (undefined4 *)0x0) {
    *puVar1 = &PTR_CMenuItem__scalar_deleting_dtor_005db440;
    puVar1[2] = *(undefined4 *)(param_1 + 8);
    puVar1[4] = *(undefined4 *)(param_1 + 0x10);
    puVar1[5] = *(undefined4 *)(param_1 + 0x14);
    puVar1[3] = *(undefined4 *)(param_1 + 0xc);
    return puVar1;
  }
  return (undefined4 *)0x0;
}
