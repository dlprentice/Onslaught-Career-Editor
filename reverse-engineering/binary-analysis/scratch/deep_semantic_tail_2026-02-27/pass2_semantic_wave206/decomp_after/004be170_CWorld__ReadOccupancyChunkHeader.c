/* address: 0x004be170 */
/* name: CWorld__ReadOccupancyChunkHeader */
/* signature: void CWorld__ReadOccupancyChunkHeader(void) */


/* WARNING: Unknown calling convention -- yet parameter storage is locked */

void CWorld__ReadOccupancyChunkHeader(void)

{
  undefined1 local_10 [4];
  undefined1 local_c [4];
  undefined1 local_8 [4];
  undefined1 local_4 [4];

  DXMemBuffer__ReadBytes(&stack0x00000004,4);
  DXMemBuffer__ReadBytes(local_10,4);
  DXMemBuffer__ReadBytes(local_c,4);
  DXMemBuffer__ReadBytes(local_8,4);
  DXMemBuffer__ReadBytes(local_4,4);
  return;
}
