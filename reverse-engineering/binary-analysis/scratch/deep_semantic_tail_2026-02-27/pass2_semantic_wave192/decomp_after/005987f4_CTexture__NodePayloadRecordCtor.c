/* address: 0x005987f4 */
/* name: CTexture__NodePayloadRecordCtor */
/* signature: int CTexture__NodePayloadRecordCtor(void) */


/* WARNING: Unknown calling convention -- yet parameter storage is locked */

int CTexture__NodePayloadRecordCtor(void)

{
  undefined4 *in_ECX;
  undefined4 in_stack_00000004;
  undefined4 in_stack_00000008;
  undefined4 in_stack_0000000c;

  in_ECX[2] = in_stack_00000004;
  in_ECX[3] = in_stack_00000008;
  in_ECX[1] = 1;
  *in_ECX = &PTR_CDXTexture__Dtor_NodePayload_DeleteOnFlag_005ef230;
  in_ECX[4] = in_stack_0000000c;
  return (int)in_ECX;
}
