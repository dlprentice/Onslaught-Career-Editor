/* address: 0x00571060 */
/* name: CFastVB__Helper_00571060 */
/* signature: bool __stdcall CFastVB__Helper_00571060(uint param_1) */


bool CFastVB__Helper_00571060(uint param_1)

{
  uint uVar1;

  uVar1 = param_1 & 0x80000001;
  if ((int)uVar1 < 0) {
    uVar1 = (uVar1 - 1 | 0xfffffffe) + 1;
  }
  return (bool)('\x01' - (uVar1 != 0));
}
