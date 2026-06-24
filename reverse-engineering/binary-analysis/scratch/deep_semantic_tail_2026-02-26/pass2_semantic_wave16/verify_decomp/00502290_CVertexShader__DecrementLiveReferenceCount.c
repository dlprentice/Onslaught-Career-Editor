/* address: 0x00502290 */
/* name: CVertexShader__DecrementLiveReferenceCount */
/* signature: void __fastcall CVertexShader__DecrementLiveReferenceCount(int param_1) */


void __fastcall CVertexShader__DecrementLiveReferenceCount(int param_1)

{
  *(int *)(param_1 + 0x30) = *(int *)(param_1 + 0x30) + -1;
  return;
}
