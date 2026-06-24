/* address: 0x00423900 */
/* name: CChunkerStream__CloseDXMemBuffer_Status0OrMinus1 */
/* signature: int CChunkerStream__CloseDXMemBuffer_Status0OrMinus1(void) */


/* WARNING: Unknown calling convention -- yet parameter storage is locked */

int CChunkerStream__CloseDXMemBuffer_Status0OrMinus1(void)

{
  int iVar1;

  iVar1 = DXMemBuffer__Close();
  return (iVar1 != 0) - 1;
}
