package edu.harvard.summer2024.cscis71.bestteamforever.DeepScan.repository;

import edu.harvard.summer2024.cscis71.bestteamforever.DeepScan.model.User;
import org.springframework.data.repository.CrudRepository;

public interface UserRepository extends CrudRepository<User, Integer> {
}
