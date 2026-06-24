/* address: 0x00549310 */
/* name: CDXMemoryManager__LogDebugStats */
/* signature: void CDXMemoryManager__LogDebugStats(void) */


/* WARNING: Unknown calling convention -- yet parameter storage is locked */

void CDXMemoryManager__LogDebugStats(void)

{
  char local_1f4 [500];

  DebugTrace(s___________________________00651144);
  DebugTrace(s_Logging_Stats_00651134);
  DebugTrace(s___________________________00651144);
  CMemoryManager__DumpStats();
  CMemoryManager__DumpStats();
  CMemoryManager__DumpStats();
  DebugTrace(s___Heap_Info___00651124);
  sprintf(local_1f4,s_Default_heap___Peak__d__Size__d_00651100);
  DebugTrace(local_1f4);
  sprintf(local_1f4,s_Thing_heap___Peak__d__Size__d_006510e0);
  DebugTrace(local_1f4);
  DebugTrace(s___________________________00651144);
  DebugTrace(s_Done_Logging_Stats_006510cc);
  DebugTrace(s___________________________00651144);
  return;
}
