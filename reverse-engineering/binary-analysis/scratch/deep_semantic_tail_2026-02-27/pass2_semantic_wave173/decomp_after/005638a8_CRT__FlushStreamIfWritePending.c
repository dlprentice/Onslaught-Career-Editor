/* address: 0x005638a8 */
/* name: CRT__FlushStreamIfWritePending */
/* signature: void __cdecl CRT__FlushStreamIfWritePending(int param_1, void * param_2) */


void __cdecl CRT__FlushStreamIfWritePending(int param_1,void *param_2)

{
  if ((param_1 != 0) && ((*(byte *)((int)param_2 + 0xd) & 0x10) != 0)) {
    CDXTexture__FlushWriteStreamSegment(param_2);
    *(byte *)((int)param_2 + 0xd) = *(byte *)((int)param_2 + 0xd) & 0xee;
    *(undefined4 *)((int)param_2 + 0x18) = 0;
    *(undefined4 *)param_2 = 0;
    *(undefined4 *)((int)param_2 + 8) = 0;
  }
  return;
}
