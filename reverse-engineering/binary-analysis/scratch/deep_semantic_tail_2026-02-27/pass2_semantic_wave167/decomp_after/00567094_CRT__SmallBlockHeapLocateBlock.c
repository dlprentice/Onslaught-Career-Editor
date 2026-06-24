/* address: 0x00567094 */
/* name: CRT__SmallBlockHeapLocateBlock */
/* signature: int __cdecl CRT__SmallBlockHeapLocateBlock(void * param_1, void * param_2, void * param_3) */


int __cdecl CRT__SmallBlockHeapLocateBlock(void *param_1,void *param_2,void *param_3)

{
  undefined **ppuVar1;
  uint uVar2;

  ppuVar1 = &PTR_LOOP_00653d80;
  while ((param_1 <= ppuVar1[4] || (ppuVar1[5] <= param_1))) {
    ppuVar1 = (undefined **)*ppuVar1;
    if (ppuVar1 == &PTR_LOOP_00653d80) {
      return 0;
    }
  }
  if (((uint)param_1 & 0xf) != 0) {
    return 0;
  }
  if (((uint)param_1 & 0xfff) < 0x100) {
    return 0;
  }
  *(undefined ***)param_2 = ppuVar1;
  uVar2 = (uint)param_1 & 0xfffff000;
  *(uint *)param_3 = uVar2;
  return ((int)((int)param_1 + (-0x100 - uVar2)) >> 4) + 8 + uVar2;
}
