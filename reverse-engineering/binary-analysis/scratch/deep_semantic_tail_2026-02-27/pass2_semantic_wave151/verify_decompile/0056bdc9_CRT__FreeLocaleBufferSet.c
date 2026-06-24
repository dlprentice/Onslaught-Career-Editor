/* address: 0x0056bdc9 */
/* name: CRT__FreeLocaleBufferSet */
/* signature: void __cdecl CRT__FreeLocaleBufferSet(int param_1) */


void __cdecl CRT__FreeLocaleBufferSet(int param_1)

{
  if ((param_1 != 0) && (*(undefined **)(param_1 + 0xc) != &DAT_009d0c28)) {
    CRT__FreeBase((int)*(undefined **)(param_1 + 0xc));
    CRT__FreeBase(*(int *)(param_1 + 0x10));
    CRT__FreeBase(*(int *)(param_1 + 0x14));
    CRT__FreeBase(*(int *)(param_1 + 0x18));
    CRT__FreeBase(*(int *)(param_1 + 0x1c));
    CRT__FreeBase(*(int *)(param_1 + 0x20));
    CRT__FreeBase(*(int *)(param_1 + 0x24));
  }
  return;
}
