package com.server.developerportfolio;

import org.bukkit.command.Command;
import org.bukkit.command.CommandExecutor;
import org.bukkit.command.CommandSender;
import org.bukkit.entity.Player;
import org.bukkit.plugin.java.JavaPlugin;
import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.util.concurrent.CompletableFuture;

public class ReportPlugin extends JavaPlugin implements CommandExecutor {

    @Override
    public void onEnable() {
        this.getCommand("reportcc").setExecutor(this);
        getLogger().info("Portfolio Report Plugin Enabled!");
    }

    @Override
    public boolean onCommand(CommandSender sender, Command cmd, String label, String[] args) {
        if (!(sender instanceof Player)) {
            sender.sendMessage("Only players can use this command.");
            return true;
        }

        if (args.length < 2) {
            sender.sendMessage("§cUsage: /reportcc <player> <reason>");
            return true;
        }

        String target = args[0];
        StringBuilder reasonBuilder = new StringBuilder();
        for (int i = 1; i < args.length; i++) {
            reasonBuilder.append(args[i]).append(" ");
        }
        String reason = reasonBuilder.toString().trim();
        String reporter = sender.getName();

        sender.sendMessage("§aSubmitting report...");
        
        // Handle network operations asynchronously to prevent server lag
        CompletableFuture.runAsync(() -> sendReportToBackend(reporter, target, reason));

        return true;
    }

    private void sendReportToBackend(String reporter, String target, String reason) {
        try {
            String json = String.format("{\"reporter\":\"%s\",\"target\":\"%s\",\"reason\":\"%s\"}", 
                reporter, target, reason);

            HttpClient client = HttpClient.newHttpClient();
            HttpRequest request = HttpRequest.newBuilder()
                    .uri(URI.create("http://localhost:3000/api/reports"))
                    .header("Content-Type", "application/json")
                    .POST(HttpRequest.BodyPublishers.ofString(json))
                    .build();

            HttpResponse<String> response = client.send(request, HttpResponse.BodyHandlers.ofString());
            
            if (response.statusCode() == 200) {
                getLogger().info("Successfully synced report for " + target + " to backend.");
            }
        } catch (Exception e) {
            getLogger().severe("Failed to send report to backend: " + e.getMessage());
        }
    }
}
