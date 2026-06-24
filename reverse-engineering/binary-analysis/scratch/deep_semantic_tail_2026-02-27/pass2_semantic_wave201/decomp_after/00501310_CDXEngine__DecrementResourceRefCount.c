/* address: 0x00501310 */
/* name: CDXEngine__DecrementResourceRefCount */
/* signature: void __fastcall CDXEngine__DecrementResourceRefCount(int param_1) */


void __fastcall CDXEngine__DecrementResourceRefCount(int param_1)

{
  *(int *)(param_1 + 0x60) = *(int *)(param_1 + 0x60) + -1;
  return;
}
